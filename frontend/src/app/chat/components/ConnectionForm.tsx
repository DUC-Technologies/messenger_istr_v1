import React from 'react';
import {useChatStore} from "@/app/store/chatStore";

const ConnectionForm = ({ handleConnect }: { handleConnect: () => void }) => {
    const { chatId, token, setChatId, setToken } = useChatStore();

    return (
        <form onSubmit={(e) => e.preventDefault()}>
            <label>
                Chat ID:
                <input type="text" value={chatId} onChange={(e) => setChatId(e.target.value)} />
            </label>
            <br />
            <label>
                Token:
                <input type="text" value={token} onChange={(e) => setToken(e.target.value)} />
            </label>
            <br />
            <button type="button" onClick={handleConnect}>
                Connect
            </button>
        </form>
    );
};

export default ConnectionForm;
