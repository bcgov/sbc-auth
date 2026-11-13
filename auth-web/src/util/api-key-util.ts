import CommonUtils from '@/util/common-util'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'

// Copy api key to the clipboard and shows a toast on success
export async function copyApiKeyToClipboard (apiKey: string, keyName: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(apiKey)
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Failed to copy API key', error)
    return false
  }
  const event: Event = { message: `API key copied: ${CommonUtils.escapeHtml(keyName)}`, type: 'default', timeout: 3000 }
  EventBus.$emit('show-toast', event)
  return true
}
