<!-- Copied from PPR. Move into sbc-common or bcrs-shared after vue 3 upgrade -->
<template>
  <v-card class="date-selection registration-date" elevation="6" ref="datePicker">
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
          color="primary"
          :max="endDate ? endDate : today"
          v-model="startDate"
        />
      </v-col>
      <v-col cols="6">
        <v-date-picker
          color="primary"
          :min="startDate ? startDate : null"
          :max="today"
          v-model="endDate"
        />
      </v-col>
    </v-row>
    <v-row no-gutters justify="end">
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
  endDate: string,
  startDate: string,
  defaultMonth: ComputedRef<string>
  today: ComputedRef<string>
}

export default defineComponent({
  name: 'DatePicker',
  props: {
    reset: { default: 1 },
    setEndDate: { type: String },
    setStartDate: { type: String }
  },
  emits: ['submit'],
  setup (props, { emit }) {
    const state = (reactive({
      datePickerErr: false,
      endDate: null,
      startDate: null,
      defaultMonth: computed((): string => {
        const todayDate = new Date()
        return todayDate.toISOString().substring(0, 8)
      }),
      today: computed((): string => {
        const todayDate = new Date()
        return todayDate.toLocaleDateString('en-CA')
      })
    }) as unknown) as DatePickerI
    const emitDateRange = (): void => {
      if (
        state.startDate === state.defaultMonth.value ||
        state.endDate === state.defaultMonth.value
      ) {
        emit('submit', { endDate: null, startDate: null })
      } else {
        emit('submit', { endDate: state.endDate, startDate: state.startDate })
      }
    }
    const resetDateRange = (): void => {
      // reset dates by setting year/month with no day (defaults back to current month)
      state.endDate = state.defaultMonth.value
      state.startDate = state.defaultMonth.value
      // set to null after to clear
      setTimeout(() => {
        state.endDate = null
        state.startDate = null
      }, 10)
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
        state.endDate = state.defaultMonth.value
        setTimeout(() => { state.endDate = null }, 10)
      } else state.endDate = val
    })
    watch(() => props.setStartDate, (val: string) => {
      if (!val) {
        state.startDate = state.defaultMonth.value
        setTimeout(() => { state.startDate = null }, 10)
      } else state.startDate = val
    })
    watch(() => props.reset, () => { console.log('reset'); resetDateRange() })

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
