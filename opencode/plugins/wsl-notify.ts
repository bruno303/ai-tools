import type { Plugin } from "@opencode-ai/plugin"

export const WslBeep: Plugin = async ({ $ }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        await $`powershell.exe -NoProfile -Command "[console]::beep(1000,700)"`.quiet()
      }
    },
  }
}
