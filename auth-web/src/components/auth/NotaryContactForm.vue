<template>
  <v-form ref="notaryContactForm" lazy-validation>
    <fieldset v-if="notaryContact">
      <legend class="mb-4">Notary Contact</legend>
      <v-row>
        <v-col cols="12" class="py-0">
          <v-text-field
            filled
            label="Email Address"
            :rules="rules.email"
            :disabled="disabled"
            hint="Optional"
            persistent-hint
            v-model.trim="notaryContact.email"
            @change="emitNotaryContact"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            label="Phone"
            :disabled="disabled"
            hint="Optional"
            persistent-hint
            v-model.trim="notaryContact.phone"
            @change="emitNotaryContact"
          >
          </v-text-field>
        </v-col>
        <v-col cols="3" class="py-0">
          <v-text-field
            filled
            label="Extension"
            :disabled="disabled"
            hint="Optional"
            persistent-hint
            v-model.trim="notaryContact.extension"
            @change="emitNotaryContact"
          >
          </v-text-field>
        </v-col>
      </v-row>
    </fieldset>
  </v-form>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { NotaryContact } from '@/models/notary'

@Component
export default class NotaryContactForm extends Vue {
  @Prop() inputNotaryContact: NotaryContact
  @Prop({ default: false }) disabled: boolean
  private notaryContact: NotaryContact = {}

  $refs: {
    notaryContactForm: HTMLFormElement,
  }

  private readonly rules = {
    email: [v => !!v || 'Email is required']
  }

  mounted () {
    if (this.inputNotaryContact) {
      Object.keys(this.inputNotaryContact).forEach(key => {
        this.$set(this.notaryContact, key, this.inputNotaryContact?.[key])
      })
    }
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

<style lang="scss" scoped></style>
