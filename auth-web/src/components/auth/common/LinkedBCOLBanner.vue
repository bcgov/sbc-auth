<template>
  <div>
  <v-alert
    dark
    color="primary"
    class="ma-0 py-3 px-5"
    v-if="!editMode"
  >
    <div class="bcol-acc d-flex justify-space-between align-center" >
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
          v-can:CHANGE_PAYMENT_METHOD.disable
        >
          Remove
        </v-btn>
      </div>

      <div>
        <v-btn v-if="showEditBtn"
          v-can:CHANGE_PAYMENT_METHOD.disable
          color="primary"
          plain
          depressed
          x-large
          class="font-weight-bold"
          @click="editAccount"
          data-test="edit-bcol-button"
        >
          <v-icon class="ml-2">mdi-pencil</v-icon>
          Edit
        </v-btn>
      </div>
    </div>
  </v-alert>
  <BcolLogin v-if="editMode" :hideLinkBtn="true" :defaultUserId="bcolAccountDetails.userId" @emit-bcol-info="emitBcolInfo" ></BcolLogin>
  </div>
</template>

<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import BcolLogin from '@/components/auth/create-account/BcolLogin.vue'

@Component({
  components: {
    BcolLogin
  }
})
export default class LinkedBCOLBanner extends Vue {
  @Prop({ default: false }) showUnlinkAccountBtn: boolean
  @Prop({ default: false }) showEditBtn: boolean
  @Prop({ default: '' }) bcolAccountName: string
  @Prop({ default: () => ({} as BcolAccountDetails) }) bcolAccountDetails: BcolAccountDetails
  private editMode: boolean = false // user can edit the bcol details

  private async mounted () {
    this.editMode = false
    this.emitBcolInfo({})
  }
  @Emit()
  private unlinkAccount () {
  }

  @Emit('emit-bcol-info')
  private emitBcolInfo (bcolProfile: BcolProfile) {
    return bcolProfile
  }

  private editAccount () {
    this.editMode = true
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
