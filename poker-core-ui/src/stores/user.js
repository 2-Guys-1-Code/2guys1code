import { defineStore } from 'pinia'

export const useUserstore = defineStore('user', {
    state: () => {
        return {
            user: null,
        }
    },
})