package com.adnan238238.aitools

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.adnan238238.aitools.databinding.ItemMessageAiBinding
import com.adnan238238.aitools.databinding.ItemMessageUserBinding

class ChatAdapter(
    private val messages: List<Message>
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val TYPE_USER = 0
        private const val TYPE_AI = 1
    }

    class UserViewHolder(val binding: ItemMessageUserBinding) : RecyclerView.ViewHolder(binding.root)
    class AiViewHolder(val binding: ItemMessageAiBinding) : RecyclerView.ViewHolder(binding.root)

    override fun getItemViewType(position: Int): Int =
        if (messages[position].isUser()) TYPE_USER else TYPE_AI

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        return if (viewType == TYPE_USER) {
            UserViewHolder(ItemMessageUserBinding.inflate(inflater, parent, false))
        } else {
            AiViewHolder(ItemMessageAiBinding.inflate(inflater, parent, false))
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val message = messages[position]
        when (holder) {
            is UserViewHolder -> holder.binding.textMessage.text = message.content
            is AiViewHolder -> holder.binding.textMessage.text = message.content
        }
    }

    override fun getItemCount(): Int = messages.size
}
