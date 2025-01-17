<template>
  <div>
    <v-divider class="my-2" />
    <div
      v-if="!isEditing"
      dark
      color="primary"
      class="ma-0"
    >
      <div class="d-flex">
        <div
          v-if="bcolAccountDetails"
          class="d-block"
        >
          <div class="font-weight-bold">
            {{ bcolAccountName }}
          </div>
          <div>Account No: <strong>{{ bcolAccountDetails.accountNumber }}</strong></div>
          <div>Prime Contact ID: <strong>{{ bcolAccountDetails.userId }}</strong></div>
        </div>
      </div>
    </div>
    <BcolLogin
      v-if="isEditing"
      :hideLinkBtn="true"
      @emit-bcol-info="emitBcolInfo"
    />
  </div>
</template>
<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { defineComponent } from '@vue/composition-api'
import BcolLogin from '@/components/auth/create-account/BcolLogin.vue'

export default defineComponent({
  name: 'LinkedBCOLBanner',
  components: {
    BcolLogin
  },
  props: {
    bcolAccountName: {
      type: String,
      default: ''
    },
    bcolAccountDetails: {
      type: Object,
      default: () => ({} as BcolAccountDetails)
    },
    isEditing: {
      type: Boolean,
      default: false
    }
  },
  emits: ['unlink-account', 'emit-bcol-info'],
  setup (props, { emit }) {
    const emitBcolInfo = (bcolProfile: BcolProfile) => {
      emit('emit-bcol-info', bcolProfile)
    }
    return {
      emitBcolInfo
    }
  }
})
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
