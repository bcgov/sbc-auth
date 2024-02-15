<template>
  <div>
    <v-alert
      type="info"
      class="my-8"
      icon="mdi-information-outline"
    >
      <strong>Temporary Passwords</strong> must be a
      <strong>minimum of 8 characters</strong> long and include the following
      characters:
      <ul class="mt-4">
        <li>include at least one uppercase character (A-Z)</li>
        <li>include at least one lowercase character (a-z)</li>
        <li>include at least one number (0-9)</li>
        <li>
          include at least one special character (examples: !, @, #, $)
        </li>
      </ul>
    </v-alert>
  </div>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'PasswordRequirementAlert'
})
</script>
<style lang="scss" scoped></style>
