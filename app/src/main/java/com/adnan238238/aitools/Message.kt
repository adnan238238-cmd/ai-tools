package com.adnan238238.aitools

import org.json.JSONArray
import org.json.JSONObject

data class Message(
    val role: String,
    val content: String
) {
    fun isUser(): Boolean = role == ROLE_USER

    fun toJson(): JSONObject = JSONObject().put("role", role).put("content", content)

    companion object {
        const val ROLE_USER = "user"
        const val ROLE_ASSISTANT = "assistant"

        fun fromJson(o: JSONObject): Message = Message(o.optString("role", ROLE_USER), o.optString("content", ""))
    }
}

object MessageStore {
    private const val KEY_HISTORY = "chat_history"

    fun load(prefs: android.content.SharedPreferences): MutableList<Message> {
        val raw = prefs.getString(KEY_HISTORY, null) ?: return mutableListOf()
        return try {
            val arr = JSONArray(raw)
            (0 until arr.length()).map { Message.fromJson(arr.getJSONObject(it)) }.toMutableList()
        } catch (e: Exception) {
            mutableListOf()
        }
    }

    fun save(prefs: android.content.SharedPreferences, messages: List<Message>) {
        val arr = JSONArray()
        messages.forEach { arr.put(it.toJson()) }
        prefs.edit().putString(KEY_HISTORY, arr.toString()).apply()
    }

    fun clear(prefs: android.content.SharedPreferences) {
        prefs.edit().remove(KEY_HISTORY).apply()
    }
}
