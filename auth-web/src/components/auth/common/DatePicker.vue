<template>
    <v-card class="date-selection registration-date" elevation="6" ref="datePicker">
        <v-row no-gutters>
            <v-col class="picker-title" :class="{ 'picker-err': startDate === null && datePickerErr }" cols="6">
                Select Start Date:
            </v-col>
            <v-col class="picker-title pl-4" :class="{ 'picker-err': endDate === null && datePickerErr }" cols="6">
                Select End Date:
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="6">
                <v-date-picker color="primary" :max="endDate ? endDate : today" v-model="startDate" />
            </v-col>
            <v-col cols="6">
                <v-date-picker color="primary" :min="startDate ? startDate : null" :max="today" v-model="endDate" />
            </v-col>
        </v-row>
        <v-row no-gutters justify="end">
            <v-col cols="auto pr-4">
                <v-btn class="date-selection-btn bold" ripple small text @click="submitDateRange()">
                    OK
                </v-btn>
                <v-btn class="date-selection-btn ml-4" ripple small text @click="resetDateRange()">
                    Cancel
                </v-btn>
            </v-col>
        </v-row>
    </v-card>
</template>

<script lang="ts">
import { Component, Emit, Prop, Watch } from 'vue-property-decorator'
import Vue from 'vue'

@Component({})
export default class DatePicker extends Vue {
    @Prop({ default: '' }) setEndDate: string
    @Prop({ default: '' }) setStartDate: string

    private datePickerErr: boolean = false
    private endDate = null
    private startDate = null

    private get defaultMonth () {
      const todayDate = new Date()
      return todayDate.toISOString().substring(0, 8)
    }

    private get today () {
      const todayDate = new Date()
      return todayDate.toLocaleDateString('en-CA')
    }

    @Emit('submit')
    private emitDateRange () {
      if (
        this.startDate === this.defaultMonth ||
            this.endDate === this.defaultMonth
      ) {
        return { endDate: '', startDate: '' }
      } else {
        return { endDate: this.endDate, startDate: this.startDate }
      }
    }

    private resetDateRange () {
      // reset dates by setting year/month with no day (defaults back to current month)
      this.endDate = this.defaultMonth
      this.startDate = this.defaultMonth
      // set to null after to clear
      setTimeout(() => {
        this.endDate = null
        this.startDate = null
      }, 10)
      this.datePickerErr = false
      this.emitDateRange()
    }

    private submitDateRange () {
      if (!this.startDate || !this.endDate) {
        this.datePickerErr = true
        return
      }
      this.datePickerErr = false
      this.emitDateRange()
    }

    @Watch('setEndDate')
    private endDateChanged (val: string) {
      if (!val) {
        this.endDate = this.defaultMonth
        setTimeout(() => {
          this.endDate = null
        }, 10)
      } else this.endDate = val
    }

    @Watch('setStartDate')
    private startDateChanged (val: string) {
      if (!val) {
        this.startDate = this.defaultMonth
        setTimeout(() => {
          this.startDate = null
        }, 10)
      } else this.startDate = val
    }
}

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
