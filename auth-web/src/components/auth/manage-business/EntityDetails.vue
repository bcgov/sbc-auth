<template>
  <IconTooltip
    :icon="icon"
    maxWidth="300px"
    :colour="iconColour"
    :iconStyling="{'font-size': '1.5em', 'margin-left': '4px'}"
    :location="{top: true}"
  >
    <div class="alert-content">
      <span v-if="showAlertHeader" class="alert-header" :style="{ 'font-weight': 'bold' }">
        {{ alertHeader }}
      </span>
      <div v-if="alertMessages && alertMessages.length == 1" class="alert-content">
        {{ alertMessages[0].message }}
      </div>
      <ul v-else class="alert-content">
        <li v-for="message, i in alertMessages" :key="i">
          {{ message.message }}
        </li>
      </ul>
    </div>
  </IconTooltip>
</template>

<script lang="ts">
import { EntityAlertTypes } from '@/util/constants'
import IconTooltip from '@/components/IconTooltip.vue'
import { PropType } from 'vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'EntityDetails',
  components: { IconTooltip },
  props: {
    details: {
      type: Array as PropType<Array<EntityAlertTypes>>,
      required: true
    },
    showAlertHeader: {
      type: Boolean
    },
    icon: {
      type: String,
      required: true
    }
  },
  setup (props) {
    const generateMessage = (status: string): { message: string, colour: string, priority: number } => {
      switch (status) {
        case EntityAlertTypes.PROCESSING:
          return { message: 'This name request is still processing, it may take up to 10 minutes.', colour: '#1669BB', priority: 5 }
        case EntityAlertTypes.FROZEN:
          return { message: 'This business is frozen', colour: '#F8661A', priority: 4 }
        case EntityAlertTypes.BADSTANDING:
          return { message: 'This business is not in good standing', colour: '#F8661A', priority: 3 }
        case EntityAlertTypes.LIQUIDATION:
          return { message: 'This business is in liquidation', colour: '#D3272C', priority: 2 }
        case EntityAlertTypes.DISSOLUTION:
          return { message: 'This business is in the process of being dissolved', colour: '#D3272C', priority: 1 }
        case EntityAlertTypes.EXPIRED:
          return { message: 'This incorporation application is no longer valid; the name request is expired.', colour: '#D3272C', priority: 5 }
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
