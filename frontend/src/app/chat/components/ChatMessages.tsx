import React from 'react';
import {useChatStore} from "@/app/store/chatStore";

const ChatMessages = () => {
    const { messageHistory } = useChatStore();

    return (
        <ul>
            {messageHistory.map((msg, idx) => (
                <li key={idx}>{msg}</li>
            ))}
        </ul>
    );
};

export default ChatMessages;
