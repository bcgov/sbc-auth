<script lang="ts">
import Component from 'vue-class-component'
import { Prop } from 'vue-property-decorator'
import Vue from 'vue'

@Component({
  name: 'Steppable'
})
export default class Steppable extends Vue {
  @Prop() stepForward!: (useAlternate?: boolean) => void
  @Prop() stepBack!: (useAlternate?: boolean) => void
  @Prop() jumpToStep!: (index: number, useAlternate?: boolean) => void
}
</script>
