<template>
  <div class="terms-container">
    <div
      v-if="!canCheckTerms"
      role="button"
      aria-label="View Terms and Conditions"
      class="terms-button"
      tab-index="0"
      @click.stop="openDialog()"
    />
    <v-checkbox
      v-model="termsAccepted"
      color="primary"
      class="terms-checkbox align-checkbox-label--top ma-0 pa-0"
      hide-details
      :disabled="!canCheckTerms"
      required
      data-test="check-termsAccepted"
      @change="emitTermsAcceptanceStatus"
    >
      <template #label>
        <span>I have read, understood and agree to the
          <strong
            class="faux-link"
            role="button"
            aria-description="Read, understand and agree to the terms of conditions"
            tabindex="0"
            @keyup.enter="openDialog()"
            @click.stop="openDialog()"
          >{{ tosText }}</strong>
          {{ tosCheckBoxLabelAppend }}
        </span>
      </template>
    </v-checkbox>
    <v-dialog
      v-model="termsDialog"
      scrollable
      width="800"
      role="dialog"
      tabindex="-1"
      aria-labelled-by="dialogTitle"
      :persistent="true"
    >
      <v-card>
        <v-card-title>
          <h2 id="dialogTitle">
            {{ tosHeading }}
          </h2>
          <v-btn
            large
            icon
            aria-label="Close Terms and Conditions Dialog"
            @click="closeDialog"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text
          id="scroll-target"
          class="py-2 px-6"
          data-test="scroll-area"
        >
          <div v-scroll:#scroll-target="onScroll">
            <TermsOfUse
              :tosType="tosType"
            />
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn
            large
            color="primary"
            class="agree-btn"
            :disabled="!atBottom"
            data-test="accept-button"
            @click="agreeToTerms"
          >
            <span>Agree to Terms</span>
          </v-btn>
          <v-btn
            large
            depressed
            data-test="close-button"
            @click="closeDialog"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed, defineComponent, onMounted, ref } from '@vue/composition-api'
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'TermsOfUseDialog',
  components: { TermsOfUse },
  props: {
    tosType: { type: String, default: 'termsofuse' },
    tosHeading: { type: String, default: 'Terms of Use Agreement' },
    tosCheckBoxLabelAppend: { type: String, default: '' },
    tosText: { type: String, default: '' },
    isUserTOS: { type: Boolean, default: false },
    isAlreadyAccepted: { type: Boolean, default: false }
  },
  setup (props, { emit }) {
    const userStore = useUserStore()
    const userHasToAcceptTOS = computed(() => userStore.userHasToAcceptTOS)
    const termsDialog = ref(false)
    const termsAccepted = ref(false)
    const canCheckTerms = ref(false)
    const atBottom = ref(false)

    const tooltipTxt = computed(() => 'Please read and agree to the Terms Of Use')

    onMounted(() => {
      termsDialog.value = false
      if (props.isUserTOS && userHasToAcceptTOS.value) {
        agreeToTerms()
      }
      if (props.isAlreadyAccepted) {
        termsAccepted.value = canCheckTerms.value = true
      }
    })

    function updateTermsAccepted (val) {
      if (props.isUserTOS && val) {
        agreeToTerms()
      }
    }

    function updateIsAlreadyAccepted (val, oldVal) {
      if (oldVal !== val) {
        termsAccepted.value = canCheckTerms.value = val
      }
    }

    function openDialog () {
      termsDialog.value = true
    }

    function closeDialog () {
      termsDialog.value = false
    }

    function onScroll (e) {
      atBottom.value = (e.target.scrollHeight - e.target.scrollTop) <= (e.target.offsetHeight + 25)
    }

    function agreeToTerms () {
      termsDialog.value = false
      termsAccepted.value = true
      canCheckTerms.value = true
      emitTermsAcceptanceStatus()
    }

    function emitTermsAcceptanceStatus () {
      emit('terms-acceptance-status', termsAccepted.value)
    }

    return {
      termsDialog,
      termsAccepted,
      canCheckTerms,
      atBottom,
      tooltipTxt,
      openDialog,
      closeDialog,
      onScroll,
      agreeToTerms,
      updateTermsAccepted,
      updateIsAlreadyAccepted,
      emitTermsAcceptanceStatus
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.terms-container {
  position: relative;
}

.terms-button {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  bottom: -0.5rem;
  left: -0.5rem;
  z-index: 4;
}

// Tighten up some of the spacing between rows
[class^='col'] {
  padding-top: 0;
  padding-bottom: 0;
}

h2 {
  max-width: 45ch;
}

.terms-checkbox {
  pointer-events: auto !important;
}

.form__btns {
  display: flex;
  justify-content: flex-end;
}

.terms-checkbox-label-btn {
  height: auto !important;
  padding: 0.25rem !important;
  font-size: 1rem !important;
  text-decoration: underline;
}

.v-card__actions {
  justify-content: center;

  .v-btn {
    width: 8rem;
  }
}

.terms-container ::v-deep {
  article {
    background: $gray1;
  }
}

.v-tooltip__content:before {
  content: ' ';
  position: absolute;
  top: -20px;
  left: 50%;
  margin-left: -10px;
  width: 20px;
  height: 20px;
  border-width: 10px 10px 10px 10px;
  border-style: solid;
  border-color: transparent transparent var(--v-grey-darken4) transparent;
}

.align-checkbox-label--top {
  ::v-deep {
    .v-input__slot {
      align-items: flex-start;
    }
    .v-label {
      color: var(--v-grey-darken3);
    }
  }
}

.v-input-checkbox {
    .v-input .v-label {
    color: var(--v-grey-darken4) !important;
  };
}

.faux-link {
  color: var(--v-primary-base);
  text-decoration: underline;
}

.agree-btn {
  font-weight: 600;
}

</style>
