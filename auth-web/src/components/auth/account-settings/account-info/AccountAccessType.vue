<template>
  <div>
    <v-form ref="accountAccessTypeForm">
      <v-card elevation="0">
        <div class="account-label">
          <div class="nav-list-title font-weight-bold pl-3" data-test="title">Access Type</div>
          <div v-if="isLoading" class="loading-inner-container loading-center">
            <v-progress-circular
              size="50"
              width="5"
              color="primary"
              :indeterminate="isLoading"
            />
          </div>

          <div class="details" v-else>
            <div v-if="viewOnlyMode" class="view-only">
              <div class="with-change-icon">
                <div>
                  <span data-test="txt-selected-access-type">{{ selectedAccessType === AccessType.GOVN ? 'Government agency (other than BC provincial)' : 'Regular Access'}}</span>
                </div>
                <div
                  v-if="canChangeAccessType && selectedAccessType !== AccessType.GOVN"
                >
                  <span
                    class="primary--text cursor-pointer"
                    @click="
                      $emit('update:viewOnlyMode', {
                        component: 'accessType',
                        mode: false
                      })
                    "
                    data-test="btn-edit"
                  >
                    <v-icon color="primary" size="20"> mdi-pencil</v-icon>
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
                :rules="[selectedAccessTypeRules]"
              >
                <v-radio
                label="Regular Access"
                :key="AccessType.REGULAR"
                :value="AccessType.REGULAR"
                data-test="radio-regular-access"
                ></v-radio>
                <v-radio
                label="Government agency (other than BC provincial)"
                :key="AccessType.GOVN"
                :value="AccessType.GOVN"
                data-test="radio-govn"
                ></v-radio>
              </v-radio-group>
              <v-card-actions class="px-0 pt-0">
                <v-row>
                  <v-col cols="12" class="form__btns py-0 d-inline-flex">
                    <div class="d-flex" v-if="!isPad">
                      <v-icon size="30" color="error" class="mt-1 mr-4">mdi-alert-circle-outline</v-icon>
                      <span class="error-text">{{ $t('accountAccessTypeUpdateWarning') }}</span>
                    </div>
                    <v-spacer></v-spacer>
                    <v-btn
                      large
                      class="save-btn px-9"
                      color="primary"
                      :loading="false"
                      aria-label="Save Account Access Type"
                      @click="updateDetails()"
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
                      @click="cancelEdit()"
                      data-test="reset-button"
                      >Cancel</v-btn>
                  </v-col>
                </v-row>
              </v-card-actions>
            </div>
          </div>
        </div>
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { AccessType, PaymentTypes } from '@/util/constants'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Organization } from '@/models/Organization'

@Component({
})
export default class AccountAccessType extends Vue {
  @Prop({ default: undefined }) organization: Organization
  @Prop({ default: true }) viewOnlyMode: boolean
  @Prop({ default: false }) canChangeAccessType: boolean
  @Prop({ default: undefined }) currentOrgPaymentType: string

  $refs: {
    accountAccessTypeForm: HTMLFormElement,
    selectedAccessType: HTMLFormElement
  }
  private selectedAccessType: string = undefined
  public AccessType = AccessType
  public isLoading = false

  public get isPad (): boolean {
    return this.currentOrgPaymentType && this.currentOrgPaymentType === PaymentTypes.PAD
  }

  // Watch property access type and update model
  @Watch('organization', { deep: true, immediate: true })
  onOrganizationChange () {
    this.selectedAccessType = this.organization.accessType === AccessType.GOVN ? AccessType.GOVN : AccessType.REGULAR
  }

  // Custom rules for selectedAccessType v-model in form
  public selectedAccessTypeRules (): any {
    return this.selectedAccessType === AccessType.GOVN ? true : 'Please select Government agency'
  }

  // Currently, there is only one way change from Regular access type accounts to GovN. Not the other way around
  public updateDetails () {
    if (this.isPad && this.$refs.accountAccessTypeForm.validate()) {
      this.$emit('update:updateAndSaveAccessTypeDetails', this.selectedAccessType)
    }
  }

  @Emit('update:viewOnlyMode')
  cancelEdit () {
    this.selectedAccessType = this.organization.accessType === AccessType.GOVN ? AccessType.GOVN : AccessType.REGULAR
    return {
      component: 'accessType',
      mode: true
    }
  }
}
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

</style>
