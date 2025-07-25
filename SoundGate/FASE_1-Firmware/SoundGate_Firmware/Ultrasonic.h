
/*
 * Ultrasonic.h - Library for HC-SR04 Ultrasonic Sensing Module.
 *
 * With ideas from:
 *   Created by ITead studio. Alex, Apr 20, 2010.
 *   iteadstudio.com
 *
 * SVN Keywords
 * ----------------------------------
 * $Author: cnobile $
 * $Date: 2011-12-07 21:49:14 -0500 (Wed, 07 Dec 2011) $
 * $Revision: 38 $
 * ----------------------------------
 *
 * Thank you to Rowan Simms for pointing out the change in header name with
 * Arduino version 1.0 and up.
 *
 */

#ifndef ULTRASONIC_H
#define ULTRASONIC_H

#include <stddef.h>


// Undefine COMPILE_STD_DEV if you don't want Standard Deviation.
#define COMPILE_STD_DEV


typedef struct bufferCtl
    {
    float *pBegin;
    float *pIndex;
    size_t length;
    bool filled;
    } BufCtl;

class Ultrasonic
    {
    public:
    Ultrasonic(int tp, int ep);
    long timing();
    float convert(long microsec, int metric);
    void setDivisor(float value, int metric);
    static const int IN = 0;
    static const int CM = 1;

#ifdef COMPILE_STD_DEV
    bool sampleCreate(size_t size, ...);
    void sampleClear();
    float unbiasedStdDev(float value, size_t bufNum);
#endif // COMPILE_STD_DEV

    private:
    int _trigPin;
    int _echoPin;
    float _cmDivisor;
    float _inDivisor;

#ifdef COMPILE_STD_DEV
    size_t _numBufs;
    BufCtl *_pBuffers;
    void _sampleUpdate(BufCtl *buf, float msec);
    void _freeBuffers();
#endif // COMPILE_STD_DEV
    };

#endif // ULTRASONIC_H

/*
 * Ultrasonic.cpp - Library for HC-SR04 Ultrasonic Sensing Module.
 *
 * With ideas from:
 *   Created by ITead studio. Apr 20, 2010.
 *   iteadstudio.com
 *
 * SVN Keywords
 * ----------------------------------
 * $Author: cnobile $
 * $Date: 2011-10-08 21:07:42 -0400 (Sat, 08 Oct 2011) $
 * $Revision: 35 $
 * ----------------------------------
 *
 * Centimeters Divisor
 * =========== =======
 *  15.875     26.9029
 *  46.355     27.6233
 *  92.075     28.1949
 * 137.795     28.4717
 * 183.515     28.5584
 * 229.235     28.5936
 * 274.955     28.7194
 *
 * Inches      Divisor
 * ======      =======
 *   6.25      68.3333
 *  18.25      70.1633
 *  36.25      71.6152
 *  54.25      72.3182
 *  72.25      72.5384
 *  90.25      72.6277
 * 108.25      72.9473
 */

#include <stdlib.h>
#include <string.h>



Ultrasonic::Ultrasonic(int tp, int ep)
    {
    pinMode(tp, OUTPUT);
    pinMode(ep, INPUT);
    _trigPin = tp;
    _echoPin = ep;
    _cmDivisor = 27.6233;
    _inDivisor = 70.1633;
    }

long Ultrasonic::timing()
    {
    digitalWrite(_trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(_trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(_trigPin, LOW);
    return pulseIn(_echoPin, HIGH);
    }

float Ultrasonic::convert(long microsec, int metric)
    {
    // microsec / 29 / 2;
    if(metric) return microsec / _cmDivisor / 2.0;  // CM
    // microsec / 74 / 2;
    else return microsec / _inDivisor / 2.0;  // IN
    }

void Ultrasonic::setDivisor(float value, int metric)
    {
    if(metric) _cmDivisor = value;
    else _inDivisor = value;
    }

#ifdef COMPILE_STD_DEV
bool Ultrasonic::sampleCreate(size_t numBufs, ...)
    {
    bool result = false;
    va_list ap;
    _numBufs = numBufs;

    if((_pBuffers = (BufCtl *) calloc(numBufs, sizeof(BufCtl))) != NULL)
        {
        va_start(ap, numBufs);
        BufCtl *buf;
        size_t smpSize;

        for(size_t i = 0; i < _numBufs; i++)
            {
            buf = &_pBuffers[i];
            smpSize = va_arg(ap, size_t);

            if((buf->pBegin = (float *) calloc(smpSize, sizeof(float))) != NULL)
                {
                buf->pIndex = buf->pBegin;
                buf->length = smpSize;
                buf->filled = false;
                result = true;
                }
            else
                {
                result = false;
                break;
                }
            }

        va_end(ap);
        }

    if(!result) _freeBuffers();
    return result;
    }

void Ultrasonic::sampleClear()
    {
    if(_pBuffers)
        {
        BufCtl *buf;

        for(size_t i = 0; i < _numBufs; i++)
            {
            buf = &_pBuffers[i];
            memset(buf, '\0', sizeof(float) * buf->length);
            buf->pIndex = buf->pBegin;
            buf->filled = false;
            }
        }
    }

float Ultrasonic::unbiasedStdDev(float value, size_t bufNum)
    {
    float result = 0.0;

    if(_pBuffers)
        {
        BufCtl *buf = &_pBuffers[bufNum];

        if(buf->length > 1)
            {
            _sampleUpdate(buf, float(value));

            if(buf->filled)
                {
                float sum = 0.0, mean, tmp;

                for(size_t i = 0; i < buf->length; i++)
                    sum += buf->pBegin[i];

                mean = sum / buf->length;
                sum = 0.0;

                for(size_t i = 0; i < buf->length; i++)
                    {
                    tmp = buf->pBegin[i] - mean;
                    sum += (tmp * tmp);
                    }

                result = sqrt(sum / (buf->length - 1));
                //Serial.print(bufNum);
                //Serial.print(" : ");
                //Serial.println(result);
                }
            }
        }

    return result;
    }

void Ultrasonic::_sampleUpdate(BufCtl *buf, float msec)
    {
    if(buf->pIndex >= (buf->pBegin + buf->length))
        {
        buf->pIndex = buf->pBegin;
        buf->filled = true;
        }

    *(buf->pIndex++) = msec;
    }

void Ultrasonic::_freeBuffers()
    {
    if(_pBuffers)
        {
        BufCtl *buf;

        for(size_t i = 0; i < _numBufs; i++)
            {
            buf = &_pBuffers[i];
            free(buf->pBegin);
            }

        free(_pBuffers);
        }
    }
#endif // COMPILE_STD_DEV