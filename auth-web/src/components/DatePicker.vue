<!-- Copied from PPR. Move into sbc-common or bcrs-shared after vue 3 upgrade -->
<template>
  <v-card
    ref="datePicker"
    class="date-selection registration-date"
    elevation="6"
  >
    <v-row no-gutters>
      <v-col
        class="picker-title"
        :class="{ 'picker-err': startDate === null && datePickerErr }"
        cols="6"
      >
        Select Start Date:
      </v-col>
      <v-col
        class="picker-title pl-4"
        :class="{ 'picker-err': endDate === null && datePickerErr }"
        cols="6"
      >
        Select End Date:
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <v-date-picker
          :key="'start' + datePickerKey"
          v-model="startDate"
          color="primary"
          :max="endDate ? endDate : today"
        />
      </v-col>
      <v-col cols="6">
        <v-date-picker
          :key="'end' + datePickerKey"
          v-model="endDate"
          color="primary"
          :min="startDate ? startDate : null"
          :max="today"
        />
      </v-col>
    </v-row>
    <v-row
      no-gutters
      justify="end"
    >
      <v-col cols="auto pr-4">
        <v-btn
          class="date-selection-btn bold"
          ripple
          small
          text
          @click="submitDateRange()"
        >
          OK
        </v-btn>
        <v-btn
          class="date-selection-btn ml-4"
          ripple
          small
          text
          @click="resetDateRange()"
        >
          Cancel
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import {
  ComputedRef,
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'

// FUTURE: remove after vue 3 upgrade
interface DatePickerI {
  datePickerErr: boolean
  datePickerKey: number
  endDate: string,
  startDate: string,
  today: ComputedRef<string>
}

export default defineComponent({
  name: 'DatePicker',
  props: {
    reset: { default: 1 },
    setEndDate: { type: String, default: null },
    setStartDate: { type: String, default: null }
  },
  emits: ['submit'],
  setup (props, { emit }) {
    const state = (reactive({
      datePickerErr: false,
      datePickerKey: 0,
      endDate: null,
      startDate: null,
      today: computed((): string => {
        const todayDate = new Date()
        const localYear = todayDate.toLocaleDateString('en-CA', { year: 'numeric', timeZone: 'America/Vancouver' })
        const localMonth = todayDate.toLocaleDateString('en-CA', { month: '2-digit', timeZone: 'America/Vancouver' })
        const localDay = todayDate.toLocaleDateString('en-CA', { day: '2-digit', timeZone: 'America/Vancouver' })
        return [localYear, localMonth, localDay].join('-')
      })
    }) as unknown) as DatePickerI

    const emitDateRange = (): void => {
      const startDate = state.startDate
      const endDate = state.endDate
      emit('submit', { endDate: endDate, startDate: startDate })
    }
    const resetDateRange = (): void => {
      state.endDate = null
      state.startDate = null
      // rerender to reset default dates (so it opens at the default date again)
      state.datePickerKey++
      state.datePickerErr = false
      emitDateRange()
    }
    const submitDateRange = (): void => {
      if (!state.startDate || !state.endDate) {
        state.datePickerErr = true
        return
      }
      state.datePickerErr = false
      emitDateRange()
    }

    watch(() => props.setEndDate, (val: string) => {
      if (!val) {
        state.endDate = null
        // rerender to reset default date (so it opens at the default date again)
        state.datePickerKey++
      } else state.endDate = val
    })
    watch(() => props.setStartDate, (val: string) => {
      if (!val) {
        state.startDate = null
        // rerender to reset default date (so it opens at the default date again)
        state.datePickerKey++
      } else state.startDate = val
    })
    watch(() => props.reset, () => { resetDateRange() })

    return {
      emitDateRange,
      resetDateRange,
      submitDateRange,
      ...toRefs(state)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.date-selection {
  border-radius: 5px;
  z-index: 10;
  left: 50%;
  margin-top: 120px;
  overflow: auto;
  padding: 24px 34px 24px 34px;
  position: absolute;
  transform: translate(-50%, 0);
  background-color: white;
  width: 700px;
  td {
    padding: 0;
  }
}
</style>
