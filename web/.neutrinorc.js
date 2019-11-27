module.exports = {
    use: [
        '@neutrinojs/standardjs',
        ['@neutrinojs/react', {
            devServer: {
                host: '127.0.0.1',
                port: parseInt(process.env.PORT || 8000, 10),
                https: false,
            },
            html: {
                title: ''
            }
        }],
        '@neutrinojs/jest',
        // Use absolute paths or it will break on nested pages...
        (neutrino)=> {
            neutrino.config.output.publicPath("/");
        },
        ['@neutrinojs/style-loader', {
            test: /\.global\.(css|sass|scss)$/,
            modulesTest: /(?<!\.global)\.(css|sass|scss)$/,
            modules: true,
            css: {
                localIdentName: '[local]--[hash:base64:8]',
            },
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
        }],
        (neutrino) => {
            neutrino.config.resolve
                    .modules
                    .add(neutrino.options.source);
        },
        ['@neutrinojs/eslint', {
            eslint: {
                plugins: ['import', 'flowtype', 'jsx-a11y', 'react'],
                rules: {
                    semi: ['error', 'always'],
                },
                baseConfig: {extends: ['eslint-config-react-app']},
            }
        }],

        // Load environment variables
        // ['@neutrinojs/env', ['API_URL']],
        ({ config }) => {
            config
                .plugin('env')
                .use(new EnvironmentPlugin({
                    'NODE_ENV': null,  // required
                    'API_URL': '',
                    'BRANCH': null,
                    'COMMIT_REF': null,
                }));
        },
    ]
};
