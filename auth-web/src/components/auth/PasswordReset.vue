<template>
  <ModalDialog
    ref="passwordResetDialog"
    :show-icon="false"
    :show-actions="false"
    :fullscreen-on-mobile="
      $vuetify.breakpoint.xsOnly ||
        $vuetify.breakpoint.smOnly ||
        $vuetify.breakpoint.mdOnly
    "
    :is-persistent="true"
    :is-scrollable="true"
    max-width="800"
  >
    <template v-slot:title>
      <span>Reset Password</span>
    </template>
    <template v-slot:text>
      <template v-if="user">√
        <p>Enter a new temporary password for user <strong>{{ user.firstname }}</strong></p>

       <PasswordRequirementAlert/>
        <v-form ref="form" class="mt-3">
          <v-row>
            <v-col cols="6">
              <v-text-field
                filled
                label="Temporary Password"
                class="ml-2"
                v-model="password"
                persistent-hint
                :hint="inputHints.password"
                :rules="passwordRules"
              ></v-text-field>
            </v-col>
          </v-row>
          <div class="form__btns">
            <v-btn
              large
              depressed
              color="primary"
              @click="changePassword"
              :loading="loading"
              :disabled="loading || !isFormValid()"
              data-test="reset-button"
            >
              <span>Reset</span>
            </v-btn>
            <v-btn
              large
              depressed
              class="ml-2"
              data-test="cancel-button"
              @click="closeDialog"
            >
              <span>Cancel</span>
            </v-btn>
          </div>
        </v-form>
      </template>
    </template>
  </ModalDialog>
</template>

<script lang="ts">
import { AddUserBody, Member, Organization } from '@/models/Organization'
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import PasswordRequirementAlert from '@/components/auth/common/PasswordRequirementAlert.vue'
import { User } from '../../models/user'

@Component({
  components: {
    ModalDialog,
    PasswordRequirementAlert
  },
  computed: {
  },
  methods: {
    ...mapActions('org', ['resetPassword'])
  }
})
export default class PasswordReset extends Vue {
  private loading = false
  private readonly resetPassword!: (AddUserBody) => Promise<void>
  private password = ''
  private user: User = { firstname: '', lastname: '', username: '' }

  private inputHints = {
    username: 'Minimum 8 characters',
    password: 'See requirements above'
  }

  $refs: {
    form: HTMLFormElement
    passwordResetDialog: ModalDialog
  }

  private users: AddUserBody[] = []

  private passwordRules = [
    value => CommonUtils.validatePasswordRules(value) || `Invalid Password`
  ]

  private created () {
    this.resetForm()
  }

  private isFormValid (): boolean {
    let isValid: boolean = false
    if (this.password) {
      isValid = CommonUtils.validatePasswordRules(this.password)
    }
    return isValid
  }

  private resetForm () {
    this.$refs.form?.reset()
  }
  public openDialog (user: User) {
    this.$refs.form?.reset()
    this.user = user
    this.$refs.passwordResetDialog.open()
  }

  public closeDialog () {
    this.$refs.passwordResetDialog.close()
  }

  private async changePassword () {
    if (this.isFormValid()) {
      // set loading state
      this.loading = true
      try {
        await this.resetPassword({
          username: this.user.username,
          password: this.password
        })
      } catch (error) {
        this.loading = false
        this.$emit('reset-error')
        return
      }

      this.resetForm()

      // emit event to let parent know the invite sequence is complete
      this.$emit('reset-complete')
      this.loading = false
    }
  }

  @Emit()
  private cancel () {
    this.resetForm()
  }
}
</script>

<style lang="scss" scoped>
</style>
