<template>
  <v-form
    ref="notaryContactForm"
    lazy-validation
  >
    <fieldset v-if="notaryContact">
      <legend class="mb-4">
        Notary Contact
      </legend>
      <v-row>
        <v-col
          cols="12"
          class="py-0"
        >
          <v-text-field
            v-model.trim="notaryContact.email"
            filled
            label="Email Address"
            :rules="rules.email"
            :disabled="disabled"
            hint="Optional"
            persistent-hint
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col
          cols="4"
          class="py-0"
        >
          <v-text-field
            v-model.trim="notaryContact.phone"
            filled
            label="Phone"
            :disabled="disabled"
            hint="Optional"
            persistent-hint
          />
        </v-col>
        <v-col
          cols="3"
          class="py-0"
        >
          <v-text-field
            v-model.trim="notaryContact.extension"
            filled
            label="Extension"
            :disabled="disabled"
            hint="Optional"
            persistent-hint
          />
        </v-col>
      </v-row>
    </fieldset>
  </v-form>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { NotaryContact } from '@/models/notary'

@Component
export default class NotaryContactForm extends Vue {
  @Prop() inputNotaryContact: NotaryContact
  @Prop({ default: false }) disabled: boolean
  notaryContact: NotaryContact = {}

  $refs: {
    notaryContactForm: HTMLFormElement,
  }

  readonly rules = {
    email: [val => {
      if (val) {
        return !!CommonUtils.validateEmailFormat(val) || 'Email is invalid'
      }
      return true
    }]
  }

  mounted () {
    if (this.inputNotaryContact) {
      Object.keys(this.inputNotaryContact).forEach(key => {
        this.$set(this.notaryContact, key, this.inputNotaryContact?.[key])
      })
    }
    this.$nextTick(() => {
      this.isFormValid()
    })
  }

  @Watch('notaryContact', { deep: true })
  async updateContact () {
    this.emitNotaryContact()
  }

  @Emit('notarycontact-update')
  emitNotaryContact () {
    this.isFormValid()
    return this.notaryContact
  }

  @Emit('is-form-valid')
  isFormValid () {
    return this.$refs.notaryContactForm.validate()
  }
}
</script>
