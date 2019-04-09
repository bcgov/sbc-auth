<template>
    <v-form class="passcode-form" ref="form">
        <div class="mb-2">
            <v-text-field
                    :rules="entityNumRules"
                    hint="Example: 123456789" req
                    label="Enter your Incorporation Number"
                    outline
                    persistent-hint
                    prepend-icon="work"
                    v-model="entityNumber"
            ></v-text-field>
        </div>
        <div>
            <v-text-field
                    :rules="entityPasscodeRules"
                    hint="Example: 123456789"
                    label="Enter your Passcode"
                    outline
                    persistent-hint
                    prepend-icon="lock"
                    v-model="passcode"
            ></v-text-field>
        </div>
        <div class="passcode-form__form-btns">
            <v-btn @click="login"
                   color="primary"
                   depressed
                   large
            >Continue to Filing
                <v-icon dark right>arrow_forward</v-icon>
            </v-btn>
        </div>
    </v-form>
</template>

<script>
    export default {
        name: 'PasscodeForm',


        data: () => ({
            valid: false,
            entityNumRules: [
                (v) => !!v || 'Incorporation Number is required',
                (v) => v.length <= 10 || 'Passcode rules here...'
            ],
            entityPasscodeRules: [
                (v) => !!v || 'Passcode is required',
                (v) => v.length <= 10 || 'Passcode rules here...'
            ]
        }),


        computed: {
            entityNumber: {
                get() {
                    return this.$store.state.entityNumber;
                },
                set(value) {
                    this.$store.commit('entityNumber', value);
                }
            },
            passcode: {
                get() {
                    return this.$store.state.passcode;
                },
                set(value) {
                    this.$store.commit('passcode', value);
                }
            }


        },
        methods: {
            login: () => {
                if (this.$refs.form.validate()) {
                    console.log('Login  called -Valid');
                } else {
                    console.log('Login  called -Invalid');
                }
            }


        }

    };
</script>

<style lang="stylus" scoped>
    @import "../assets/styl/theme.styl"

    .v-input
        max-width 25rem

    .passcode-form__form-btns
        text-align center

</style>
