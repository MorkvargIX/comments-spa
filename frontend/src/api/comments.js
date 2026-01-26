import { api } from "./http.js";

export function fetchComments (params = {}) {
    return api.get('/comments/', { params })
}

export function createComment (data) {
    return api.post('/comments/', { data })
}

export function fetchReplies (commentId, params = {}) {
    return api.get(`/comments/${commentId}/replies/`, { params })
}
