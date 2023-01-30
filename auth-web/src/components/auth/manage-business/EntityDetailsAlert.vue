<!-- TODO:
        get overlay colour
        get alert icon colour
        get header font and font size
        compute array so that instead of mock arrays we get passed an array
            of statuses then turn that array of statuses into an array of messages
            then render those messages instead
        align alert icon with bottom of status
        change names of variables from status to something else
         -->

<template>
   <v-tooltip top color="grey darken-4">
     <template v-slot:activator="{ on }">
       <v-icon :color=iconColour v-on="on">mdi-alert</v-icon>
     </template>
     <div class="py-2" :style="{'max-width': '300px'}">
        <span>
            {{ alertMessage }}
        </span>
        <ul>
            <li v-for="message, i in detailMessages" :key="i">
                {{ message.message }}
            </li>
        </ul>
     </div>
   </v-tooltip>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, ref } from '@vue/composition-api'
import { EntityDetailTypes } from '@/util/constants'
import { PropType } from 'vue'

export default defineComponent({
  name: 'EntityDetailsAlert',
  props: {
    statuses: Array as PropType<Array<String>>
  },
  setup (props) {
    // testing for now
    const mockArray = ['FROZEN', 'BAD_STANDING', 'DISSOLUTION', 'LIQUIDATION'] as Array<String>

    // actual stuff

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

    const detailMessages = computed(() => {
      let temp = []
      for (let detail of mockArray) {
        temp.push(generateMessage(detail))
      }
      temp.sort(compareMessages)
      return temp
    })

    const alertMessage = computed(() => {
      return detailMessages.value.length > 1 ? 'Alerts' : 'Alert'
    })

    const iconColour = computed(() => {
      return detailMessages.value[0].colour
    })

    return {
      detailMessages,
      alertMessage,
      iconColour
    }
  }
})
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
.v-tooltip__content:after {
  content: ' ';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -10px;
  width: 20px;
  height: 20px;
  border-width: 10px 10px 10px 10px;
  border-style: solid;
  border-color: transparent transparent var(--v-grey-darken4) transparent;
  transform: rotate(180deg);
}
</style>
