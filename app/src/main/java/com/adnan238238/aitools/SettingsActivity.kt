package com.adnan238238.aitools

import android.content.SharedPreferences
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.adnan238238.aitools.databinding.ActivitySettingsBinding

class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private lateinit var prefs: SharedPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefs = getSharedPreferences("ai_tools", MODE_PRIVATE)
        binding.inputApiKey.setText(prefs.getString("api_key", ""))

        binding.btnSave.setOnClickListener {
            val key = binding.inputApiKey.text?.toString()?.trim().orEmpty()
            prefs.edit().putString("api_key", key).apply()
            android.widget.Toast.makeText(this, R.string.api_key_saved, android.widget.Toast.LENGTH_SHORT).show()
            finish()
        }
    }
}
