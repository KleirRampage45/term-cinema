# Maintainer: Asukate

pkgname=term-cinema
pkgver=0.2.0
pkgrel=1
pkgdesc="Konsole-friendly terminal video player built around Bad Apple"
arch=('any')
url="https://github.com/KleirRampage45/term-cinema"
license=('GPL3')
depends=('python' 'ffmpeg' 'chafa' 'mpv')
source=() # No remote source for now as we are building locally

package() {
  # Install the main executable directly to /usr/bin
  install -Dm755 "${srcdir}/../ascii_player.py" "${pkgdir}/usr/bin/ascii-player"

  # Install the badapple wrapper
  install -Dm755 "${srcdir}/../badapple.sh" "${pkgdir}/usr/bin/badapple"

  # Install internal modules
  mkdir -p "${pkgdir}/usr/share/ascii-player/player"
  install -Dm644 "${srcdir}/../player/"*.py "${pkgdir}/usr/share/ascii-player/player/"
  install -Dm644 "${srcdir}/../README.md" "${pkgdir}/usr/share/doc/${pkgname}/README.md"

  # Install the demo video
  if [ -f "${srcdir}/../badapple.mp4" ]; then
    install -Dm644 "${srcdir}/../badapple.mp4" "${pkgdir}/usr/share/ascii-player/badapple.mp4"
  fi
}
