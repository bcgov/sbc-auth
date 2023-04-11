<template>
      <v-container v-if="user">
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
              @click="cancel"
            >
              <span>Cancel</span>
            </v-btn>
          </div>
        </v-form>
      </v-container>
</template>

<script lang="ts">
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PasswordRequirementAlert from '@/components/auth/common/PasswordRequirementAlert.vue'
import { AddUserBody } from '@/models/Organization'
import { User } from '@/models/user'
import CommonUtils from '@/util/common-util'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapActions } from 'vuex'

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
  @Prop() private user: User

  private inputHints = {
    username: 'Minimum 8 characters',
    password: 'See requirements above'
  }

  $refs: {
    form: HTMLFormElement
    passwordResetDialog: PasswordReset
  }

  private users: AddUserBody[] = []

  private passwordRules = [
    value => CommonUtils.validatePasswordRules(value) || `Invalid Password`
  ]

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

  @Emit()
  private cancel () {
    this.resetForm()
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
}
</script>

<style lang="scss" scoped>
    .form__btns {
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
    }
</style>
