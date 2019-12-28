// Load .env file
require('dotenv').config()


// const { EnvironmentPlugin } = require('webpack');
const SERVER_PORT = parseInt(process.env.PORT || 8000, 10);


const react = require('@neutrinojs/react');
const styles = require('@neutrinojs/style-loader');
const devServer = require('@neutrinojs/dev-server');
const eslint = require('@neutrinojs/eslint');
const jest = require('@neutrinojs/jest');


module.exports = {
    options: {
        root: __dirname,
    },
    use: [

        // Lint presets must be defined prior to any other presets
        eslint({
            eslint: {
                plugins: ['import', 'flowtype', 'jsx-a11y', 'react'],
                rules: {
                    semi: ['error', 'always'],
                },
                baseConfig: {extends: ['eslint-config-react-app']},
            }
        }),

        // Resolve modules from ``src`` folder
        (neutrino) => {
            neutrino.config.resolve.modules
                    .add('node_modules')
                    .add(neutrino.options.source);
        },

        react({

            html: {
                title: 'Mowaki Application'
            },

            publicPath: '/',

            // Disable javascript minification in development mode
            minify: {
                source: process.env.NODE_ENV === 'production',
            },

            env: {
                NODE_ENV: null,  // required
                API_URL: '',
            },

            style: {
                test: /\.global\.(css|sass|scss)$/,
                modulesTest: /(?<!\.global)\.(css|sass|scss)$/,
                modules: true,
                loaders: [
                    // WARNING: Loaders need to be in *reverse* order (for
                    // some obscure reason), i.e. postcss-loader needs to be
                    // listed *before* sass-loader.
                    {
                        loader: 'postcss-loader',
                        options: {
                            plugins: [
                                require('autoprefixer')({
                                    flexbox: 'no-2009',
                                }),
                            ]
                        }
                    },
                    {
                        loader: 'sass-loader',
                        useId: 'sass',
                        options: {
                            includePaths: ['node_modules', 'src'],
                            localIdentName: '[local]--[hash:base64:8]',
                        }
                    },
                ]
            },

            devServer: {
                // Note: ``host`` doesn't seem to be honored,
                // i.e. development server will always listen on 0.0.0.0.
                // Make sure you have a firewall in place if
                // connecting to a public network.
                host: 'localhost',
                port: SERVER_PORT,
                hot: true,
            },
        }),

        jest(),
    ]
};
