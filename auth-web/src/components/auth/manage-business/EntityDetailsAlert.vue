<template>
  <IconTooltip
    icon="mdi-alert"
    maxWidth="300px"
    :colour="iconColour"
    :iconStyling="{'font-size': '1.5em', 'margin-left': '4px'}"
    :location="{top: true}"
  >
    <div class="alert-content">
      <span class="alert-header" :style="{ 'font-weight': 'bold' }">
        {{ alertHeader }}
      </span>
      <ul class="alert-content">
        <li v-for="message, i in alertMessages" :key="i">
          {{ message.message }}
        </li>
      </ul>
    </div>
  </IconTooltip>
</template>

<script lang="ts">
import { EntityDetailTypes } from '@/util/constants'
import IconTooltip from '@/components/IconTooltip.vue'
import { PropType } from 'vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'EntityDetailsAlert',
  components: { IconTooltip },
  props: {
    details: {
      type: Array as PropType<Array<EntityDetailTypes>>,
      required: true
    }
  },
  setup (props) {
    const generateMessage = (status: String): { message: String, colour: String, priority: Number } => {
      switch (status) {
        case EntityDetailTypes.FROZEN:
          return { message: 'This business is frozen', colour: '#F8661A', priority: 4 }
        case EntityDetailTypes.BADSTANDING:
          return { message: 'This business is not in good standing', colour: '#F8661A', priority: 3 }
        case EntityDetailTypes.LIQUIDATION:
          return { message: 'This business is in liquidation', colour: '#D3272C', priority: 2 }
        case EntityDetailTypes.DISSOLUTION:
          return { message: 'This business is in the process of being dissolved', colour: '#D3272C', priority: 1 }
        default:
          return null
      }
    }

    const compareMessages = (m1, m2) => {
      if (m1.priority < m2.priority) {
        return -1
      }
      if (m1.priority > m2.priority) {
        return 1
      }
      return 0
    }

    const makeMessages = () => {
      let temp = []
      for (let detail of props.details) {
        temp.push(generateMessage(detail))
      }
      temp.sort(compareMessages)
      return temp
    }

    const alertMessages = makeMessages()
    const alertHeader = alertMessages.length > 1 ? 'Alerts:' : 'Alert:'
    const iconColour = alertMessages[0].colour

    return {
      alertMessages,
      alertHeader,
      iconColour
    }
  }
})
</script>
