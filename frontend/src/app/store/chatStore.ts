import create from 'zustand';

interface ChatState {
    socketUrl: string | null;
    messageHistory: string[];
    chatId: string;
    token: string;
    message: string;
    setSocketUrl: (url: string | null) => void;
    setMessageHistory: (history: string[]) => void;
    addMessage: (message: string) => void;
    setChatId: (id: string) => void;
    setToken: (token: string) => void;
    setMessage: (message: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
    socketUrl: null,
    messageHistory: [],
    chatId: 'foo',
    token: 'some-key-token',
    message: '',
    setSocketUrl: (url) => set({ socketUrl: url }),
    setMessageHistory: (history) => set({ messageHistory: history }),
    addMessage: (message) => set((state) => ({ messageHistory: [...state.messageHistory, message] })),
    setChatId: (id) => set({ chatId: id }),
    setToken: (token) => set({ token: token }),
    setMessage: (message) => set({ message: message }),
}));
