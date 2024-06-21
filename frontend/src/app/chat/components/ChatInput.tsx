import React from 'react';
import {useChatStore} from "@/app/store/chatStore";

const ChatInput = ({ handleSendMessage }: { handleSendMessage: () => void }) => {
    const { message, setMessage } = useChatStore();

    return (
        <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}>
            <label>
                Message:
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleSendMessage(); } }}
                />
            </label>
            <button type="submit">Send</button>
        </form>
    );
};

export default ChatInput;
