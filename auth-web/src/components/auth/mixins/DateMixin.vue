// You can declare a mixin as the same style as components.
<script lang="ts">
import Component from 'vue-class-component'
import Vue from 'vue'

@Component({
  name: 'DateMixin'
})
export default class DateMixin extends Vue {
  /**
   * Converts a Date object to a date string (Month Day, Year) in Pacific timezone.
   * @example "2021-01-01 07:00:00 GMT" -> "December 31, 2020"
   * @example "2021-01-01 08:00:00 GMT" -> "January 1, 2021"
   */
  dateToPacificDate (date: Date): string {
    let dateStr = date.toLocaleDateString('en-CA', {
      timeZone: 'America/Vancouver',
      month: 'long', // December
      day: 'numeric', // 31
      year: 'numeric' // 2020
    })

    // remove period after month
    dateStr = dateStr.replace('.', '')
    return dateStr
  }
}
</script>
