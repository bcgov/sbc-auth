<template>
  <ModalDialog
    ref="dialog"
    :title="$t('vendorLinkingAccessDeniedTitle')"
    :show-icon="false"
    :show-close-icon="true"
    dialog-class="warning-dialog vendor-linking-access-denied-dialog"
    max-width="650"
    data-test="vendor-linking-access-denied-modal"
    @close-dialog="$emit('close')"
  >
    <template #text>
      <p class="vendor-linking-access-denied-dialog__text mb-0">
        {{ $t('vendorLinkingAccessDeniedBodyIntro') }}
        <a
          v-if="adminEmail"
          :href="mailtoLink"
        >{{ adminEmail }}</a><span v-if="adminEmail">.</span>
      </p>
    </template>
    <template #actions>
      <v-btn
        large
        color="primary"
        class="font-weight-bold px-8"
        data-test="vendor-linking-access-denied-close"
        @click="close()"
      >
        {{ $t('vendorLinkingAccessDeniedClose') }}
      </v-btn>
    </template>
  </ModalDialog>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from '@vue/composition-api'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

export default defineComponent({
  name: 'VendorLinkingAccessDeniedModal',
  components: {
    ModalDialog
  },
  props: {
    adminEmail: {
      type: String,
      default: ''
    }
  },
  emits: ['close'],
  setup (props) {
    const dialog = ref<InstanceType<typeof ModalDialog> | null>(null)

    const mailtoLink = computed(() => {
      return props.adminEmail ? `mailto:${props.adminEmail}` : ''
    })

    const open = () => {
      dialog.value?.open?.()
    }

    const close = () => {
      dialog.value?.close?.()
    }

    return {
      close,
      dialog,
      mailtoLink,
      open
    }
  }
})
</script>

<style lang="scss" scoped>
.vendor-linking-access-denied-dialog__text {
  color: var(--COLOR_GRAY7);
  font-size: var(--FONT_SIZE_TEXT);
  text-align: left;
}
</style>
