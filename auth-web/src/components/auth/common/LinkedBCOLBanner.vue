<template>
  <v-alert
    dark
    color="primary"
    class="ma-0 py-3 px-5"
  >
    <div class="bcol-acc d-flex justify-space-between align-center">
      <div v-if="bcolAccountDetails">
        <div class="bcol-acc__name font-weight-bold">
          {{ bcolAccountName }}
        </div>
        <ul class="bcol-acc__meta">
          <li>
            Account No: <strong>{{ bcolAccountDetails.accountNumber }}</strong>
          </li>
          <li>
            Prime Contact ID: <strong>{{ bcolAccountDetails.userId }}</strong>
          </li>
        </ul>
      </div>
      <div v-if="showUnlinkAccountBtn">
        <v-btn
          outlined
          class="font-weight-bold"
          @click="unlinkAccount"
          data-test="unlink-bcol-button"
        >
          Remove
        </v-btn>
      </div>
    </div>
  </v-alert>
</template>

<script lang="ts">
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { BcolAccountDetails } from '@/models/bcol'

@Component({})
export default class LinkedBCOLBanner extends Vue {
  @Prop({ default: false }) showUnlinkAccountBtn: boolean
  @Prop({ default: '' }) bcolAccountName: string
  @Prop({ default: () => ({} as BcolAccountDetails) }) bcolAccountDetails: BcolAccountDetails

  @Emit()
  private unlinkAccount () {
  }
}
</script>

<style lang="scss" scoped>
.bcol-acc {
  margin-top: 1px;
  margin-bottom: 2px;
}

.bcol-acc__meta {
  margin: 0;
  padding: 0;
  list-style-type: none;

  li {
    position: relative;
    display: inline-block
  }

  li + li {
    &:before {
      content: ' | ';
      display: inline-block;
      position: relative;
      top: -2px;
      width: 2rem;
      vertical-align: top;
      text-align: center;
    }
  }
}
</style>
