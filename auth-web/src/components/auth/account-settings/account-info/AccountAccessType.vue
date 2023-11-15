<template>
  <div>
    <v-form>
      <v-card elevation="0">
        <div class="account-label">
          <div
            class="nav-list-title font-weight-bold pl-3"
            data-test="title"
          >
            Access Type
          </div>
          <div
            v-if="isLoading"
            class="loading-inner-container loading-center"
          >
            <v-progress-circular
              size="50"
              width="5"
              color="primary"
              :indeterminate="isLoading"
            />
          </div>

          <div
            v-else
            class="details"
          >
            <div
              v-if="viewOnlyMode"
              class="view-only"
            >
              <div class="with-change-icon">
                <div>
                  <span data-test="txt-selected-access-type">{{ getAccessTypeText }}</span>
                </div>
                <div
                  v-if="isChangeButtonEnabled"
                >
                  <span
                    class="primary--text cursor-pointer"
                    data-test="btn-edit"
                    @click="
                      $emit('update:viewOnlyMode', {
                        component: 'accessType',
                        mode: false
                      })
                    "
                  >
                    <v-icon
                      color="primary"
                      size="20"
                    > mdi-pencil</v-icon>
                    Change
                  </span>
                </div>
              </div>
            </div>
            <div v-else>
              <v-radio-group
                v-model="selectedAccessType"
                class="mt-0"
                req
              >
                <v-radio
                  :key="AccessType.REGULAR"
                  label="Regular Access"
                  :value="AccessType.REGULAR"
                  data-test="radio-regular-access"
                />
                <v-radio
                  :key="AccessType.GOVN"
                  label="Government agency (other than BC provincial)"
                  :value="AccessType.GOVN"
                  data-test="radio-govn"
                />
              </v-radio-group>

              <v-card-actions class="px-0 pt-0">
                <v-row>
                  <v-col
                    cols="12"
                    class="form__btns py-0 d-inline-flex"
                  >
                    <v-spacer />
                    <v-btn
                      large
                      class="save-btn px-9"
                      color="primary"
                      :loading="false"
                      aria-label="Save Account Access Type"
                      @click="updateDetails(false)"
                    >
                      <span class="save-btn__label">Save</span>
                    </v-btn>
                    <v-btn
                      outlined
                      large
                      depressed
                      class="ml-2 px-9"
                      color="primary"
                      aria-label="Cancel Account Access Type"
                      data-test="reset-button"
                      @click="cancelEdit()"
                    >
                      Cancel
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-actions>
            </div>
          </div>
        </div>
      </v-card>
    </v-form>
    <!-- Confirm Access Type To Regular Dialog -->
    <ModalDialog
      ref="changeAccessTypeToRegularDialog"
      title="Change Access Type To Regular?"
      text="Regular access will not have the option to modify product fees."
      dialog-class="notify-dialog"
      max-width="680"
      :isPersistent="true"
      data-test="modal-suspension-complete"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          depressed
          class="font-weight-bold btn-dialog"
          data-test="btn-confirm-change-access-type-dialog"
          color="primary"
          @click="updateDetails(true)"
        >
          Confirm
        </v-btn>
        <v-btn
          outlined
          large
          depressed
          class="btn-dialog"
          color="primary"
          data-test="btn-cancel-change-access-type-dialog"
          @click="closeDialog"
        >
          Cancel
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { AccessType, Account } from '@/util/constants'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { reactive, computed, defineComponent, watch, toRefs } from '@vue/composition-api'

export default defineComponent({
  name: 'AccountAccessType',
  components: {
    ModalDialog
  },
  props: {
    organization: {
      type: Object,
      default: undefined,
    },
    viewOnlyMode: {
      type: Boolean,
      default: true,
    },
    canChangeAccessType: {
      type: Boolean,
      default: false,
    },
    currentOrgPaymentType: {
      type: String,
      default: undefined,
    },
  },
  emits: ['update:updateAndSaveAccessTypeDetails', 'update:viewOnlyMode'],
  setup(props , { emit }) {
      // const AccessType = AccessType
      const state = reactive({
        changeAccessTypeToRegularDialog: null,
        selectedAccessType: undefined,
        isLoading: false,
        // Only allow PREMIUM -> GOVN and GOVN -> PREMIUM
        isChangeButtonEnabled: computed<boolean>(() => {
          // Check access type and orgtype must be premium
          const accessType: any = props.organization.accessType
          const isAllowedAccessType = props.organization.orgType === Account.PREMIUM &&
            [AccessType.REGULAR, AccessType.EXTRA_PROVINCIAL, AccessType.REGULAR_BCEID, AccessType.GOVN].includes(accessType)
          return isAllowedAccessType && props.canChangeAccessType // canChangeAccessType is the role based access passed as a property
        }),
        getAccessTypeText: computed<string>(() => {
          let accessTypeText = 'Regular Access'
          if (props.organization.accessType === AccessType.GOVN) {
            accessTypeText = 'Government agency (other than BC provincial)'
          } else if (props.organization.accessType === AccessType.GOVM) {
            accessTypeText = 'BC Government Ministry'
          }
          return accessTypeText
        })
      })

      const updateDetails = (confirmed: boolean) => {
        if (state.selectedAccessType === AccessType.REGULAR && !confirmed) {
          state.changeAccessTypeToRegularDialog.open()
        } else {
          emit('update:updateAndSaveAccessTypeDetails', state.selectedAccessType)
          state.changeAccessTypeToRegularDialog.close()
        }
      }

      const closeDialog = () => {
        state.changeAccessTypeToRegularDialog.close()
      }

      const cancelEdit = () => {
        state.selectedAccessType = props.organization.accessType === AccessType.GOVN ? AccessType.GOVN : AccessType.REGULAR
        emit('update:viewOnlyMode', {
          component: 'accessType',
          mode: true
        })
      }

      // Watch property access type and update model
      watch(() => props.organization, (newVal) => {
        state.selectedAccessType = newVal.accessType === AccessType.GOVN ? AccessType.GOVN : AccessType.REGULAR
      }, { deep: true, immediate: true })


      return {
        AccessType,
        ...toRefs(state),
        updateDetails,
        closeDialog,
        cancelEdit
      }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.form__btns {
  display: flex;
  justify-content: flex-end;
}
.error-text{
  color: var(--v-error-base) !important;
}

.btn-dialog {
  height: 2.75em;
  width: 6.25em;
}
</style>
