<!-- TODO:
        get overlay colour
        get alert icon colour
        get header font and font size
        get body font and font size
        get amount of spacing between header and alert body
        get amount of spacing between each list item in the body
        get amount of spacing of alert content ie: margins and padding
        get amount of spacing of alert icon relative to org status ie: margins and padding
        compute array so that instead of mock arrays we get passed an array
            of statuses then turn that array of statuses into an array of messages
            then render those messages instead
        align alert icon with bottom of status
         -->

<template>
    <v-tooltip top>
        <template v-slot:activator="{ on, attrs }">
              <v-icon color="red" v-bind="attrs" v-on="on">
                mdi-alert
              </v-icon>
        </template>
        <div>
            <h3>
                Alerts:
            </h3>
            <ul>
                <li v-for="status, i in mockArray" :key="status + i">
                    {{ status }}
                </li>
            </ul>
        </div>
    </v-tooltip>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'EntityStatusAlert',
  props: {
    statuses: []
  },
  setup (props) {
    const mockArray = ['STATUS1', 'STATUS2', 'STATUS3']
    return {
      mockArray
    }
  }
})
</script>
