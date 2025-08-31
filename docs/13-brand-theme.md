# Brand & theme

### Colors
- **Primary**: Blue #216093, White #FFFFFF
- **Secondary**: Navy Blue #001B48, Teal #57949A, Light Gray #F9FAFA, Black #000000
- **Tertiary**: Orange #E18331, Green #2E933C, Red #DB162F, Medium Blue #224870, Yellow #F0C319

### Vuetify theme (TypeScript)
```ts
// frontend/src/app/theme.ts
import { createVuetify } from 'vuetify'

export const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#216093',
          secondary: '#001B48',
          info: '#224870',
          success: '#2E933C',
          warning: '#F0C319',
          error: '#DB162F',
          background: '#F9FAFA',
          surface: '#FFFFFF',
          onBackground: '#000000',
        },
      },
    },
  },
})
```

### Usage
Import and register `vuetify` in your `main.ts`, and keep feature components color-agnostic (use `color="primary"|"secondary"|...`).