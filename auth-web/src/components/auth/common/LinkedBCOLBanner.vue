<template>
  <div>
    <v-alert
      v-if="!editMode"
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
            v-can:CHANGE_PAYMENT_METHOD.disable
            outlined
            class="font-weight-bold"
            data-test="unlink-bcol-button"
            @click="unlinkAccount"
          >
            Remove
          </v-btn>
        </div>

        <div>
          <v-btn
            v-if="showEditBtn"
            v-can:CHANGE_PAYMENT_METHOD.disable
            color="primary"
            plain
            depressed
            x-large
            class="font-weight-bold"
            data-test="edit-bcol-button"
            @click="editAccount"
          >
            <v-icon class="ml-2">
              mdi-pencil
            </v-icon>
            Edit
          </v-btn>
        </div>
      </div>
    </v-alert>
    <BcolLogin
      v-if="editMode"
      :hideLinkBtn="true"
      @emit-bcol-info="emitBcolInfo"
    />
  </div>
</template>
<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { onMounted, ref } from '@vue/composition-api'
import BcolLogin from '@/components/BcolLogin.vue'

export default {
  name: 'LinkedBCOLBanner',
  components: {
    BcolLogin
  },
  props: {
    showUnlinkAccountBtn: {
      type: Boolean,
      default: false
    },
    showEditBtn: {
      type: Boolean,
      default: false
    },
    forceEditMode: {
      type: Boolean,
      default: false
    },
    bcolAccountName: {
      type: String,
      default: ''
    },
    bcolAccountDetails: {
      type: Object,
      default: () => ({} as BcolAccountDetails)
    }
  },
  setup (props, { emit }) {
    const editMode = ref(false)

    // Set editMode based on props or details
    onMounted(() => {
      editMode.value = props.forceEditMode || Object.keys(props.bcolAccountDetails).length === 0 || false
    })

    const unlinkAccount = () => {
      emit('unlink-account')
    }

    const emitBcolInfo = (bcolProfile: BcolProfile) => {
      emit('emit-bcol-info', bcolProfile)
    }

    const editAccount = () => {
      editMode.value = true
    }

    return {
      editMode,
      unlinkAccount,
      emitBcolInfo,
      editAccount
    }
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
