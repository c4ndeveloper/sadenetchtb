from skpy import SkypeEventLoop, SkypeNewMessageEvent, SkypeChat
import re

class SkypeBot(SkypeEventLoop):
    def __init__(self, username, password, source_group_id, target_groups, log_group_id):
        super().__init__(username, password)
        self.source_group_id = source_group_id
        self.target_groups = target_groups
        self.log_group_id = log_group_id
        self.is_running = True  # Assume the bot is running initially

        # Find the source group chat and send "Status: ON" message
        source_group = self.chats.chat(self.source_group_id)
        source_group.sendMsg("Status: ON")

    def onEvent(self, event):
        if not self.is_running:
            return  # Stop processing events if the bot is no longer running

        if isinstance(event, SkypeNewMessageEvent):
            msg = event.msg
            if msg.chat.id == self.source_group_id and msg.type == "RichText":
                message_content = msg.content
                if "ty zdes bot?" in message_content.lower():
                    self.respond_ty_zdes_bot(msg)

                for tag, target_group_id in self.target_groups.items():
                    if tag in message_content:
                        self.forward_message(msg, target_group_id)
                        self.log_message(msg)  # Log the forwarded message

    def respond_ty_zdes_bot(self, msg):
        source_chat = self.chats.chat(msg.chat.id)
        sender_name = f"{msg.user.name.first} {msg.user.name.last}"
        source_chat.sendMsg(f"Yes, I am here {sender_name}")

    def log_message(self, msg):
        log_group = self.chats.chat(self.log_group_id)
        sender_name = f"{msg.user.name.first} {msg.user.name.last}"
        log_content = f"From: {sender_name}\nMessage: {msg.content}"
        log_group.sendMsg(log_content)

    def forward_message(self, msg, target_group_id):
        target_group = self.chats.chat(target_group_id)
        sender_name = f"{msg.user.name.first} {msg.user.name.last}"

        # Remove <a href= and </a> tags from the message content
        cleaned_content = re.sub(r'<a\s*.*?>|</a>', '', msg.content)
        # Remove parts containing "#" character
        cleaned_content = re.sub(r'#\w+', '', cleaned_content)
        
        # Show the message at the top and the sender at the bottom
        forwarded_message = f"{cleaned_content.strip()}\n\n{sender_name}"
        target_group.sendMsg(forwarded_message)
        print("Message forwarded:", forwarded_message, "Target group ID:", target_group_id)

        # Find the chat of the message to send a reply "Forwarded [sender name]"
        source_chat = self.chats.chat(msg.chat.id)
        source_chat.sendMsg(f"Forwarded Mr./Ms. {sender_name}")

    def watchdog(self):
        # Set the is_running flag to False to stop the bot
        self.is_running = False

        # Send the exit command to terminate the loop
        self.conn.close()
