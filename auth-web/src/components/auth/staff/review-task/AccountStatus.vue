<template>
  <div id="account-status">
    <h2 class="mb-5">
      {{ `${tabNumber !==null ? `${tabNumber}.` : ''} ${title}` }}
    </h2>
    <v-row>
      <v-col class="col-12 col-sm-5 py-2">
        Status
      </v-col>
      <v-col
        class="py-2"
        :class="{'error--text font-weight-bold': (isTaskRejected) }"
      >
        {{ statusLabel }}
      </v-col>
    </v-row>
    <v-row v-if="isAccountOnHold">
      <v-col class="col-12 col-sm-5 py-2">
        Reason(s)
      </v-col>
      <v-col class="py-2">
        <ul class="remark-display pl-0">
          <li
            v-for="(remark, index) in accountOnHoldRemarks"
            :key="index"
            class="pb-1"
          >
            <span
              class="font-weight-bold"
              :data-test="`text-number-${index}`"
            > {{ formatNumberToTwoPlaces(index+1) }}. </span>
            <span
              class="pl-1"
              :data-test="`text-remark-${index}`"
            > {{ remark }} </span>
          </li>
        </ul>
      </v-col>
    </v-row>
    <v-row v-if="!isPendingReviewPage">
      <v-col class="col-12 col-sm-5 py-2">
        <span v-if="taskDetails.relationshipStatus === TaskRelationshipStatus.ACTIVE">Approved By</span>
        <span v-if="isTaskRejected">Rejected By</span>
      </v-col>
      <v-col
        v-if="!isPendingReviewPage"
        class="py-2"
      >
        {{ taskDetails.modifiedBy }}<br>
        {{ formatDate(taskDetails.modified) }}
      </v-col>
    </v-row>
    <v-row v-if="accountOnHoldRemarks && isTaskRejected">
      <v-col
        cols="5"
        class="py-2"
      >
        Reason(s)
      </v-col>
      <v-col
        cols="7"
        class="py-2"
      >
        <span>{{ accountOnHoldRemarks && accountOnHoldRemarks[0] }}</span>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="col-12 col-sm-5 py-2">
        Created On
      </v-col>
      <v-col class="py-2">
        {{ formatDate(taskDetails.created) }}
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { TaskRelationshipStatus, TaskStatus } from '@/util/constants'
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { Task } from '@/models/Task'
import moment from 'moment'

export default defineComponent({
  name: 'AccountStatusTab',
  props: {
    tabNumber: { type: Number, default: null },
    isPendingReviewPage: { type: Boolean, required: false },
    title: { type: String, default: 'Account Status' },
    taskDetails: { type: Object as () => Task, default: () => null }
  },
  setup (props) {
    const formatNumberToTwoPlaces = CommonUtils.formatNumberToTwoPlaces
    const localState = reactive({
      isAccountOnHold: computed(() => props.taskDetails?.status === TaskStatus.HOLD),
      isTaskRejected: computed(() => props.taskDetails?.relationshipStatus === TaskRelationshipStatus.REJECTED),
      accountOnHoldRemarks: computed(() => props.taskDetails?.remarks),
      statusLabel: computed((): string => {
        switch (props.taskDetails.relationshipStatus) {
          case TaskRelationshipStatus.ACTIVE:
            return 'Approved'
          case TaskRelationshipStatus.REJECTED:
            return 'Rejected'
          case TaskRelationshipStatus.PENDING_STAFF_REVIEW:
            // Eg, If the task for BCEID account review is on hold then we display the status as "on hold" else "pending"
            return localState.isAccountOnHold ? 'On Hold' : 'Pending'
          default:
            return ''
        }
      })
    })
    const formatDate = (date: Date): string => {
      return moment(date).format('MMM DD, YYYY')
    }

    return {
      formatDate,
      formatNumberToTwoPlaces,
      TaskRelationshipStatus,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
  #account-status {
    max-width: 23.75rem;
  }
  .remark-display {
    list-style-type: none;
  }
</style>
