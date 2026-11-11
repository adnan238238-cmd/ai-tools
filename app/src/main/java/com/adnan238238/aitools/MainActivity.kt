package com.adnan238238.aitools

import android.content.SharedPreferences
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.adnan238238.aitools.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var prefs: SharedPreferences
    private val messages = mutableListOf<Message>()
    private val adapter by lazy { ChatAdapter(messages) }
    private var pendingCall: okhttp3.Call? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefs = getSharedPreferences("ai_tools", MODE_PRIVATE)

        binding.recyclerChat.layoutManager = LinearLayoutManager(this).apply {
            stackFromEnd = true
        }
        binding.recyclerChat.adapter = adapter

        binding.btnSettings.setOnClickListener { openSettings() }
        binding.btnClear.setOnClickListener { confirmClearChat() }
        binding.btnSend.setOnClickListener { sendMessage() }

        messages.addAll(MessageStore.load(prefs))
        adapter.notifyDataSetChanged()
        scrollToBottom()
        updateEmptyState()
    }

    private fun hasApiKey(): Boolean =
        prefs.getString("api_key", "")?.isNotBlank() == true

    private fun openSettings() {
        val view = layoutInflater.inflate(R.layout.dialog_settings, null)
        val input = view.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.input_api_key)
        input.setText(prefs.getString("api_key", ""))

        AlertDialog.Builder(this)
            .setTitle(R.string.api_key)
            .setView(view)
            .setPositiveButton(R.string.save) { _, _ ->
                val key = input.text?.toString()?.trim().orEmpty()
                prefs.edit().putString("api_key", key).apply()
                updateEmptyState()
                if (key.isNotBlank()) {
                    android.widget.Toast.makeText(this, R.string.api_key_saved, android.widget.Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton(android.R.string.cancel, null)
            .show()
    }

    private fun confirmClearChat() {
        AlertDialog.Builder(this)
            .setMessage(R.string.clear_chat)
            .setPositiveButton(android.R.string.ok) { _, _ ->
                pendingCall?.cancel()
                messages.clear()
                MessageStore.clear(prefs)
                adapter.notifyDataSetChanged()
                updateEmptyState()
            }
            .setNegativeButton(android.R.string.cancel, null)
            .show()
    }

    private fun sendMessage() {
        val text = binding.inputMessage.text?.toString()?.trim().orEmpty()
        if (text.isEmpty()) return

        if (!hasApiKey()) {
            openSettings()
            return
        }

        appendMessage(Message(Message.ROLE_USER, text))
        binding.inputMessage.setText("")
        setLoading(true)

        val client = MistralClient(prefs.getString("api_key", "")!!)
        pendingCall = client.chat(messages.toList(), object : MistralClient.Callback2 {
            override fun onSuccess(reply: String) {
                runOnUiThread {
                    setLoading(false)
                    appendMessage(Message(Message.ROLE_ASSISTANT, reply))
                }
            }

            override fun onError(message: String) {
                runOnUiThread {
                    setLoading(false)
                    appendMessage(Message(Message.ROLE_ASSISTANT, getString(R.string.error_prefix, message)))
                }
            }
        })
    }

    private fun appendMessage(message: Message) {
        messages.add(message)
        adapter.notifyItemInserted(messages.size - 1)
        MessageStore.save(prefs, messages)
        scrollToBottom()
        updateEmptyState()
    }

    private fun setLoading(loading: Boolean) {
        binding.progress.visibility = if (loading) View.VISIBLE else View.GONE
        binding.btnSend.isEnabled = !loading
    }

    private fun scrollToBottom() {
        if (messages.isNotEmpty()) {
            binding.recyclerChat.post { binding.recyclerChat.smoothScrollToPosition(messages.size - 1) }
        }
    }

    private fun updateEmptyState() {
        val empty = messages.isEmpty()
        binding.textEmpty.setText(
            if (hasApiKey()) R.string.welcome else R.string.no_api_key
        )
        binding.textEmpty.visibility = if (empty) View.VISIBLE else View.GONE
    }
}
