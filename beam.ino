#include <Adafruit_NeoPixel.h>

#define PIN2 2
#define PIN4 4
#define PIN6 6
#define PIN9 9
#define PIN7 7

int pirState = LOW;
int val = 0;
int motionSensor = PIN7;

// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
Adafruit_NeoPixel strips [2] = {
  Adafruit_NeoPixel(153, PIN6, NEO_RGB + NEO_KHZ800),
  Adafruit_NeoPixel(153, PIN9, NEO_RGB + NEO_KHZ800),
};

void setup() {
  uint16_t i;

  for (i=0; i<2; i++) {
    strips[i].begin();
    strips[i].show();  // Initialize all pixels to 'off'
  }

}

void loop() {
  rainbow(100);
  // clear(10000);
}

void rainbow(uint8_t wait) {
  uint16_t i, k, j;

  for(j=0; j<256; j++) {
    for(k=0; k<2; k++) {
      for(i=0; i<strips[k].numPixels(); i++) {
        strips[k].setPixelColor(i, Wheel(&strips[k], (i+j) & 255));
      }
      strips[k].show();
    }
    delay(wait);
  }
}

void clear(uint8_t wait) {
  uint16_t i, k;

  for(k=0; k<2; k++) {
    for(i=0; i<strips[k].numPixels(); i++) {
      strips[k].setPixelColor(i, 127, 127, 127);
    }
    strips[k].show();
  }
  delay(wait);

}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(Adafruit_NeoPixel *strip, byte WheelPos) {
  if(WheelPos < 85) {
   return strip->Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  } else if(WheelPos < 170) {
   WheelPos -= 85;
   return strip->Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else {
   WheelPos -= 170;
   return strip->Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
}
