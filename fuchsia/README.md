# Fuchsia-specific CLDR data files

The boolean setting `fuchsia_uses_separate_icu_data` from `//config.gni`
determines which CLDR data dir is used when building Fuchsia code:

* When `true`: Fuchsia build will use `//fuchsia:icudtl.dat`.
* When `false`: Fuchsia build will use  `//common:icudtl.dat`.

This flag allows Fuchsia builds to use different CLDR data in some low-storage
situations.

The file `//fuchsia/icudtl.dat` is created as a simple copy of
`//common/icudtl.dat`, on demand, on a time-delayed schedule.  This allows
Fuchsia build to control when `icudtl.dat` content is updated, while not
affecting other builds.

The setting applies only when building the Fuchsia repository proper, not when
compiling software to run on Fuchsia.

## Updating `//fuchsia/icudtl.dat`

From the root directory of the ICU repository do:

```
cp common/icudtl.dat fuchsia/
```

Thereafter, make a git change as usual.
