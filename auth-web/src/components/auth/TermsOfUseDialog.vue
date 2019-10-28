<template>
    <v-row>
        <v-col sm="12">
            <v-checkbox  v-on:change="emitStatus()" color="default" v-model="termsAccepted" required on>
                <template v-slot:label>
                    <div class="terms-checkbox-label">
                        <span>I have read and agreed to the</span>
                        <v-btn text color="primary" class="pr-1 pl-1" @click.stop="termsDialog = true">
                            Terms of Use
                        </v-btn>
                    </div>
                </template>
            </v-checkbox>
            <v-dialog scrollable width="1024" v-model="termsDialog">
                <v-card>
                    <v-card-title>Terms of Use</v-card-title>
                    <v-card-text id="scroll-target">
                        <div v-scroll:#scroll-target="onScroll" style="height: 2000px;">
                            <p v-html="content"></p>
                        </div>
                    </v-card-text>
                    <v-card-actions>
                        <v-btn large depressed color="primary" class="agree-btn"
                               @click="termsDialog = false ;termsAccepted = true ;emitStatus()">
                            <span>Agree to Terms</span>
                        </v-btn>
                        <v-btn large depressed color="primary" class="agree-btn"
                               @click="termsDialog = false ;emitStatus()">
                            <span>Close</span>
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </v-col>
    </v-row>

</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import documentService from '@/services/document.service.ts'
import { getModule } from 'vuex-module-decorators'

  @Component({
    directives: {}
  })
export default class TermsOfServiceDialog extends Vue {
    @Prop({ default: '' })
    lastAcceptedVersion: string
    private termsDialog = false
    private offsetTop = '0'
    private termsAccepted = false
    private content: string = ''
    private version: string = ''

    mounted () {
      // TODO may be , cache the file somewhere in session storage or so.repeated service calls are not necessary
      documentService.getTermsOfService('termsofuse').then(response => {
        this.content = response.data.content
        this.version = response.data.version_id
      })
    }
    @Watch('lastAcceptedVersion')
    onVersionChanged (val: string, oldVal: string) {
      if (val === this.version) {
        this.termsAccepted = true
        this.emitStatus()
      }
    }

    onScroll (e) {
      this.offsetTop = e.target.scrollTop
    }

    emitStatus () {
      this.$emit('termsupdated', { 'termsversion': this.version, 'istermsaccepted': this.termsAccepted })
    }
}
</script>

<style lang="scss" scoped>
    @import '../../assets/scss/theme.scss';

    // Tighten up some of the spacing between rows
    [class^="col"] {
        padding-top: 0;
        padding-bottom: 0;
    }

    .form__btns {
        display: flex;
        justify-content: flex-end;
    }

    .terms-checkbox-label {
        display: flex;
        align-items: center;

        .v-btn {
            height: auto;
            margin-left: 0.1rem;
            padding: 0.2rem;
            text-decoration: underline;
            font-size: 1rem;
        }
    }

    .v-card__actions {
        justify-content: center;

        .v-btn {
            width: 10rem;
        }
    }
</style>
