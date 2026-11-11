package com.adnan238238.aitools

import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class MistralClient(private val apiKey: String) {

    interface Callback2 {
        fun onSuccess(reply: String)
        fun onError(message: String)
    }

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    fun chat(history: List<Message>, callback: Callback2): Call {
        val messages = JSONArray()
        messages.put(
            JSONObject()
                .put("role", "system")
                .put("content", "You are a helpful AI assistant inside the AI Tools Android app. Reply in the same language the user writes in (Bangla or English).")
        )
        history.forEach { messages.put(it.toJson()) }

        val body = JSONObject()
            .put("model", "mistral-small-latest")
            .put("messages", messages)
            .toString()
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("https://api.mistral.ai/v1/chat/completions")
            .header("Authorization", "Bearer $apiKey")
            .post(body)
            .build()

        val call = client.newCall(request)
        call.enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback.onError(e.message ?: "Network error")
            }

            override fun onResponse(call: Call, response: Response) {
                val text = response.body?.string() ?: ""
                if (!response.isSuccessful) {
                    val msg = try {
                        JSONObject(text).optJSONObject("message")?.optString("message")
                    } catch (e: Exception) {
                        null
                    } ?: "HTTP ${response.code}"
                    callback.onError(msg)
                    return
                }
                try {
                    val reply = JSONObject(text)
                        .getJSONArray("choices")
                        .getJSONObject(0)
                        .getJSONObject("message")
                        .getString("content")
                    callback.onSuccess(reply.trim())
                } catch (e: Exception) {
                    callback.onError("Unexpected response")
                }
            }
        })
        return call
    }
}
