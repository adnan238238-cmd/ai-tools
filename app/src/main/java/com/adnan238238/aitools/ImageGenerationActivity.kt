package com.adnan238238.aitools

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.adnan238238.aitools.databinding.ActivityImageGenBinding
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.URLEncoder
import java.util.concurrent.TimeUnit

class ImageGenerationActivity : AppCompatActivity() {

    private lateinit var binding: ActivityImageGenBinding
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .build()

    private var currentBitmap: Bitmap? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityImageGenBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnBack.setOnClickListener { finish() }
        binding.btnGenerate.setOnClickListener { generate() }
        binding.btnSave.setOnClickListener { saveImage() }
    }

    private fun generate() {
        val prompt = binding.inputPrompt.text?.toString()?.trim().orEmpty()
        if (prompt.isEmpty()) {
            Toast.makeText(this, R.string.prompt_required, Toast.LENGTH_SHORT).show()
            return
        }

        setLoading(true)
        binding.btnSave.isEnabled = false

        CoroutineScope(Dispatchers.Main).launch {
            val bitmap = withContext(Dispatchers.IO) {
                val encoded = URLEncoder.encode(prompt, "UTF-8").replace("+", "%20")
                val url = "https://image.pollinations.ai/prompt/$encoded?width=1024&height=1024&nologo=true&seed=${System.currentTimeMillis() % 100000}"
                val request = Request.Builder().url(url).build()
                client.newCall(request).execute().use { response ->
                    if (!response.isSuccessful) error("HTTP ${response.code}")
                    response.body?.bytes()?.let { BitmapFactory.decodeByteArray(it, 0, it.size) }
                        ?: error("Invalid image")
                }
            }
            currentBitmap = bitmap
            binding.imageResult.setImageBitmap(bitmap)
            binding.btnSave.isEnabled = true
            setLoading(false)
        }
    }

    private fun saveImage() {
        val bitmap = currentBitmap ?: return
        val name = "ai_tools_${System.currentTimeMillis()}.jpg"
        val values = android.content.ContentValues().apply {
            put(android.provider.MediaStore.Images.Media.DISPLAY_NAME, name)
            put(android.provider.MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            put(android.provider.MediaStore.Images.Media.RELATIVE_PATH, "Pictures/AI Tools")
        }
        val uri = contentResolver.insert(android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
        if (uri == null) {
            Toast.makeText(this, R.string.save_failed, Toast.LENGTH_SHORT).show()
            return
        }
        CoroutineScope(Dispatchers.Main).launch {
            val ok = withContext(Dispatchers.IO) {
                contentResolver.openOutputStream(uri)?.use { out ->
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 95, out)
                } ?: false
            }
            Toast.makeText(
                this@ImageGenerationActivity,
                if (ok) R.string.image_saved else R.string.save_failed,
                Toast.LENGTH_SHORT
            ).show()
        }
    }

    private fun setLoading(loading: Boolean) {
        binding.progress.visibility = if (loading) View.VISIBLE else View.GONE
        binding.btnGenerate.isEnabled = !loading
        binding.inputPrompt.isEnabled = !loading
    }
}
