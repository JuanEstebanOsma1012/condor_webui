#!/bin/bash

# Uso: ./montecarlo_pi.sh <num_samples>
# Ejemplo: ./montecarlo_pi.sh 1000000

if [ $# -ne 1 ]; then
  echo "Uso: $0 <num_samples>"
  exit 1
fi

num_samples=$1
inside=0

for ((i=0; i<num_samples; i++)); do
  # Generar dos números aleatorios entre 0 y 1 usando $RANDOM
  x=$(awk -v r=$RANDOM 'BEGIN {print r/32767}')
  y=$(awk -v r=$RANDOM 'BEGIN {print r/32767}')

  # Calcular x^2 + y^2 y verificar si está dentro del círculo
  inside_check=$(awk -v x=$x -v y=$y 'BEGIN {if (x*x + y*y <= 1) print 1; else print 0}')
  inside=$((inside + inside_check))
done

pi=$(awk -v inside=$inside -v total=$num_samples 'BEGIN {print 4*inside/total}')
echo "Samples: $num_samples"
echo "Estimación de Pi: $pi"
