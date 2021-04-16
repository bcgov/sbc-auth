<template>
  <div>
    <h2 class="mb-5">{{`${tabNumber !==null ?  `${tabNumber}.` : ''} ${title}`}}</h2>
    <v-row>
      <v-col class="col-12 col-sm-5 py-2">Status</v-col>
      <v-col class="py-2"   :class="{'error--text font-weight-bold': (taskDetails.relationshipStatus===TaskRelationshipStatusEnum.REJECTED) }"
          >{{ statusLabel }}
          </v-col>
    </v-row>
    <v-row v-if="!isPendingReviewPage">
      <v-col class="col-12 col-sm-5 py-2">
        <span v-if="taskDetails.relationshipStatus === TaskRelationshipStatusEnum.ACTIVE">Approved By</span>
        <span v-if="taskDetails.relationshipStatus === TaskRelationshipStatusEnum.REJECTED">Rejected By</span>
      </v-col>
      <v-col class="py-2" v-if="!isPendingReviewPage">
        {{ taskDetails.modifiedBy }}<br/>
        {{ formatDate(taskDetails.modified) }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="col-12 col-sm-5 py-2">Created On</v-col>
      <v-col class="py-2">{{ formatDate(taskDetails.created) }}</v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Task } from '@/models/Task'
import { TaskRelationshipStatus } from '@/util/constants'
import moment from 'moment'

@Component({})
export default class AccountStatusTab extends Vue {
  @Prop({ default: null }) private tabNumber: number
  @Prop({ default: false }) private isPendingReviewPage: boolean
  @Prop({ default: 'Account Status' }) private title: string
  @Prop({ default: {} }) taskDetails: Task
  public TaskRelationshipStatusEnum = TaskRelationshipStatus

  private get statusLabel (): string {
    switch (this.taskDetails.relationshipStatus) {
      case TaskRelationshipStatus.ACTIVE:
        return 'Approved'
      case TaskRelationshipStatus.REJECTED:
        return 'Rejected'
      case TaskRelationshipStatus.PENDING_STAFF_REVIEW:
        return 'Pending'
      default:
        return ''
    }
  }
  private formatDate (date: Date): string {
    return moment(date).format('MMM DD, YYYY')
  }
}
</script>
