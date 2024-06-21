import React from 'react';
import {useChatStore} from "@/app/store/chatStore";
import { ReadyState } from 'react-use-websocket';

const ChatStatus = ({ readyState }: { readyState: ReadyState }) => {
    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];

    return <h2>Connection Status: {connectionStatus}</h2>;
};

export default ChatStatus;
