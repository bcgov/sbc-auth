<template>
  <!-- vue 3: variant="accordian" -->
  <v-expansion-panels accordion>
    <v-expansion-panel class="pa-8">
      <!-- vue 3: v-expansion-panel-title -->
      <v-expansion-panel-header class="px-0">
        <slot
          name="header"
          :info="info"
          :title="title"
        >
          <header>
            <h2
              v-if="title"
              class="mb-0"
            >
              {{ title }}
            </h2>
            <p
              v-if="info"
              class="mt-3 mb-0"
              v-html="info"
            />
          </header>
        </slot>
        <template #actions>
          <slot name="actions">
            <v-icon large>
              mdi-chevron-down
            </v-icon>
          </slot>
        </template>
      </v-expansion-panel-header>
      <!-- vue 3: v-expansion-panel-text -->
      <v-expansion-panel-content>
        <slot
          name="content"
          :content="content"
        >
          {{ content }}
        </slot>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>
<script>
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'BaseVExpansionPanel',
  props: {
    content: { default: '' },
    info: { default: '' },
    title: { default: '' }
  },
  setup () {}
})
</script>
