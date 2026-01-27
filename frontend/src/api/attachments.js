import { api } from './http'

export async function fetchAttachmentText(url) {
  const { data } = await api.get(url, {
    responseType: 'text',
  })
  return data
}
