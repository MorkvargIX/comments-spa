import { api } from "./http.js";

export function fetchCaptcha() {
    return api.get('/captcha/')
}
