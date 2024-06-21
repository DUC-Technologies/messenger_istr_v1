"use client"
import React, {useEffect, useCallback} from 'react';
import useWebSocket from 'react-use-websocket';
import {useChatStore} from "@/app/store/chatStore";
import ConnectionForm from './components/ConnectionForm';
import ChatInput from './components/ChatInput';
import ChatMessages from './components/ChatMessages';
import ChatStatus from './components/ChatStatus';

const ChatPage = () => {
    const {socketUrl, setSocketUrl, addMessage, chatId, token, message, setMessage} = useChatStore();

    const {sendMessage, lastMessage, readyState} = useWebSocket(socketUrl ?? '', {
        onOpen: () => console.log('WebSocket connection established.'),
        onClose: () => console.log('WebSocket connection closed.'),
        onMessage: (event) => {
            addMessage(event.data);
        },
        shouldReconnect: (closeEvent) => true, // попытка переподключения
    });

    useEffect(() => {
        if (lastMessage !== null) {
            addMessage(lastMessage.data);
        }
    }, [lastMessage, addMessage]);

    const handleConnect = useCallback(() => {
        setSocketUrl(`ws://localhost:46020/messenger/chats/${chatId}/ws?token=${token}`);
    }, [chatId, token, setSocketUrl]);

    const handleSendMessage = useCallback(() => {
        sendMessage(message);
        setMessage('');
    }, [message, sendMessage, setMessage]);

    return (
        <div>
            <h1>WebSocket Chat</h1>
            <ConnectionForm handleConnect={handleConnect}/>
            <hr/>
            <ChatInput handleSendMessage={handleSendMessage}/>
            <ChatStatus readyState={readyState}/>
            <ChatMessages/>
        </div>
    );
};

export default ChatPage;
