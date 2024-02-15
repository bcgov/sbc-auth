<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  // eslint-disable-next-line vue/multi-word-component-names
  name: 'Steppable',
  props: {
    stepForward: {
      type: Function,
      required: true
    },
    stepBack: {
      type: Function,
      required: true
    },
    jumpToStep: {
      type: Function,
      required: true
    }
  }
})
</script>
